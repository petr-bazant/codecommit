"""
 Assigns users permissions to upsource matching that of AWS CodeCommit.
"""
import argparse,json,base64,requests,time,datetime,collections

MAX_UPSOURCE_REQUESTS=3
emailToUserIdMap = {}
userIdToEmailMap = {}

def logit(str):
  str = unicode(datetime.datetime.now()) + " - " + str
  # by default do not log to stdout or it will interfere with terraform
  #with open('upsource.log', 'a') as fp:
  #  fp.write(str + '\n')
  print(str)
  return

def constructRepoToUserIdsMap(userToReposMap, emailToUserIdMap):
  repoToUsersMap = {}
  for user in userToReposMap.keys():
    # Combine the read and write access lists
    repoCsv = userToReposMap[user][0]
    if repoCsv != "":
      repoCsv += ","
    repoCsv += userToReposMap[user][1]
    repos = repoCsv.split(",")

    # Loop through all repos assigned to this user
    for repo in repos:
      repo = repo.strip()
      if repo != "":      
        # Add user to repo, create new user list if first user added to repo
        users = repoToUsersMap.get(repo)
        if users == None:
          users = set([])
          repoToUsersMap[repo] = users
        users.add(emailToUserIdMap[user])
  
  return repoToUsersMap

def convertRepoToProject(repoToUserIdsMap, repoProjectOverrides):
  projectToUserIdsMap = {}
  # Swap out repos with Upsource project names, for those repos where the Upsource ID doesn't match
  # Also, convert any repo name with underscores to use hyphens
  for repo in repoToUserIdsMap:
    project = repoProjectOverrides.get(repo)
    if project == None:
      project = repo.replace('_','-')
    projectDetails = {}
    projectDetails["repo"] = repo 
    projectDetails["users"] = repoToUserIdsMap[repo]
    projectToUserIdsMap[project] = projectDetails
  return projectToUserIdsMap

def difference(list1, list2):
  c1 = collections.Counter(list1)
  c2 = collections.Counter(list2)
  result = (c1 - c2).keys()
  return result

def hubRequest(url, user, password, method, data):
  result = ""
  if url[-1] != '/':
    url += '/'
  url += 'hub/api/rest/'
  url += method
  attempt = 0
  while attempt < MAX_UPSOURCE_REQUESTS:
    logit("Sending Hub request; url=" + url + "; user=" + user + "; data=" + str(data))
    if data == 'DELETE':
      response = requests.delete(url, verify=False, auth=(user,password))
    elif data != None:
      response = requests.post(url, json=data, verify=False, auth=(user,password))
    else:
      response = requests.get(url, verify=False, auth=(user,password))
    logit("Received Hub response; code=" + str(response.status_code) + "; reason=" + response.reason + "; data=" + response.text)
    response.raise_for_status()
    if response.status_code == requests.codes.ok:
      try:
        result = response.json()
      except ValueError:
        result = ""
      break
    time.sleep(1)
    attempt += 1

  return result

def upsourceRequest(upsourceUrl, user, password, method, data):
  result = ""
  if upsourceUrl[-1] != '/':
    upsourceUrl += '/'
  url = upsourceUrl + '~rpc/' + method
  attempt = 0
  while attempt < MAX_UPSOURCE_REQUESTS:
    logit("Sending Upsource request; url=" + url + "; user=" + user + "; data=" + str(data))
    response = requests.post(url, json=data, verify=False, auth=(user,password))
    logit("Received Upsource response; code=" + str(response.status_code) + "; reason=" + response.reason + "; data=" + response.text)
    response.raise_for_status()
    if response.status_code == requests.codes.ok:
      result = response.json()
      break
    time.sleep(1)
    attempt += 1

  return result

def configureProject(upsourceUrl, user, password, project, request, maxAttempts, pause):
  attempts = 0
  while attempts < maxAttempts:
    logit("Waiting briefly before attempting to configure project; project=" + project + "; waitSeconds=" + str(pause))
    time.sleep(pause)
    response = upsourceRequest(upsourceUrl, user, password, "setProjectSetting", request)
    if response.get('error') != None:
      logit("Failed to configure project setting, waiting to retry; project=" + project)
    else:
      break
    attempts += 1

def createProject(upsourceUrl, user, password, project, vcsUrl, vcsPrivateKey):
  mapping = {}
  mapping['vcs'] = 'git'
  mapping['url'] = vcsUrl
  mapping['key'] = vcsPrivateKey
  mapping['mapping'] = ''
  mapping['id'] = ''
  vcs = {}
  vcs['mappings'] = [mapping]
  settings = {}
  settings['projectName'] = project
  settings['codeReviewIdPattern'] = project + '-CR-{}'
  settings['checkIntervalSeconds'] = 300
  settings['createUserGroups'] = False
  settings['projectModel'] = {'type':'none', 'pathToModel':''}
  settings['runInspections'] = True
  settings['inspectionProfileName'] = None
  settings['mavenSettings'] = ''
  settings['mavenProfiles'] = ''
  settings['modelConversionSystemProperties'] = ''
  settings['mavenJdkName'] = None
  settings['gradleProperties'] = ''
  settings['gradleInitScript'] = ''
  settings['javascriptLanguageLevel'] = 'none'
  settings['phpLanguageLevel'] = None
  settings['phpExternalDependencies'] = None
  settings['phpComposerScript'] = None
  settings['pythonLanguageLevel'] = None
  settings['buildStatusReceiveToken'] = ''
  settings['skipFileContentsImport'] = ['*.bin','*.dll','*.exe','*.so'] 
  settings['ignoredFilesInReview'] = None
  settings['defaultBranch'] = 'master'
  settings['defaultEncoding'] = ''
  settings['authorCanCloseReview'] = True
  settings['authorCanDeleteReview'] = True
  settings['limitResolveDiscussion'] = False
  settings['vcsSettings'] = json.dumps(vcs)
  request = {}
  request['newProjectId'] = project
  request['settings'] = settings
  response = upsourceRequest(upsourceUrl, user, password, "createProject", request)
  if response.get('error') != None:
    logit("Failed to create new project, aborting; project=" + project)
    raise Exception("failed to create project")

  trigger = {}
  trigger['branchWildcard'] = None
  trigger['branchWildcardExcluded'] = None
  trigger['pathWildcard'] = None
  trigger['pathWildcardExcluded'] = None
  trigger['authorUserId'] = None
  trigger['areInclusiveAuthors'] = True
  trigger['doRequireIssue'] = True
  trigger['doTrackBranch'] = False
  trigger['assigneesUsersIds'] = None
  workflowValue = {}
  workflowValue['isEnabled'] = True
  workflowValue['triggers'] = [trigger]
  workflow = {}
  workflow['key'] = 'NewRevisionWatch'
  workflow['value'] = json.dumps(workflowValue)
  request = {}
  request['projectId'] = project
  request['request'] = workflow
  configureProject(upsourceUrl, user, password, project, request, 25, 10)

  trigger = {}
  trigger['authorUserId'] = None
  trigger['areInclusiveAuthors'] = True
  trigger['doTrackReviewId'] = True
  trigger['doTrackIssueId'] = True
  trigger['doSkipMerges'] = False
  workflowValue = {}
  workflowValue['isEnabled'] = True
  workflowValue['triggers'] = [trigger]
  workflow = {}
  workflow['key'] = 'CommitAddition-NewRevisionWatch'
  workflow['value'] = json.dumps(workflowValue)
  request = {}
  request['projectId'] = project
  request['request'] = workflow
  configureProject(upsourceUrl, user, password, project, request, 10, 1)

  trigger = {}
  trigger['authorUserId'] = None
  trigger['areInclusiveAuthors'] = True
  trigger['reviewerUserId'] = None
  trigger['areInclusiveReviewers'] = True
  workflowValue = {}
  workflowValue['isEnabled'] = True
  workflowValue['triggers'] = [trigger]
  workflow = {}
  workflow['key'] = 'ReviewClosingWatch'
  workflow['value'] = json.dumps(workflowValue)
  request = {}
  request['projectId'] = project
  request['request'] = workflow
  configureProject(upsourceUrl, user, password, project, request, 10, 1)

def createUser(upsourceUrl, user, password, newUser):
  username = newUser
  atIdx = newUser.find("@")
  if atIdx > 0:
    username = newUser[0:atIdx]
  request = {}
  request['details'] = [{'type':'EmailuserdetailsJSON','email':{'type':'EmailJSON','email':newUser,'verified':True},'passwordChangeRequired':False}]
  request['name'] = username
  response = hubRequest(upsourceUrl, user, password, "users?fields=id", request)
  userId = response.get('id')
  if userId == None:
    logit("Failed to create new user, ignoring; user=" + newUser)
  return userId

def fetchUsers(hubUrl, user, password):
  emailToIdMap = {}
  response = hubRequest(hubUrl, user, password, "users?fields=id,details/email&$top=-1", None)
  for user in response.get('users'):
    details = user.get('details')
    if details != None:
      for detail in details:
        emailMap = detail.get('email')
        if emailMap != None:
          emailToIdMap[emailMap.get('email')] = user.get('id')
          break
  return emailToIdMap

def fetchProjects(upsourceUrl, user, password):
  projects = []
  response = upsourceRequest(upsourceUrl, user, password, "getAllProjects", {})
  projectResult = response['result'].get('project')
  if projectResult != None:
    for project in projectResult:
      projects.append(project.get('projectId'))
  return projects

def syncUsersWithUpsource(hubUrl, user, password, users):
  emailToUserIdMap = fetchUsers(hubUrl, user, password)
  # Create new users, if needed
  for repoUser in users:
    foundUser = emailToUserIdMap.get(repoUser)
    if foundUser == None:
      logit("Creating new user; user=" + repoUser)
      userId = createUser(hubUrl, user, password, repoUser)
      emailToUserIdMap[repoUser] = userId
  return emailToUserIdMap

def syncProjectsWithUpsource(upsourceUrl, user, password, newProjectsMap, vcsUrl, vcsPrivateKey):
  projectToUserIdsMap = {}
  projects = fetchProjects(upsourceUrl, user, password)

  if vcsUrl[-1] != '/':
    vcsUrl += '/'

  # Create any missing project
  createList = difference(newProjectsMap.keys(), projects)
  for project in createList:
    logit("Project not available in Upsource, creating new; project=" + project)
    createProject(upsourceUrl, user, password, project, vcsUrl + newProjectsMap.get(project).get("repo"), vcsPrivateKey)
    projectToUserIdsMap[project] = []

  # Query existing projects to find all users that have access
  for project in projects:
    users = []
    request = {}
    request['projectId'] = project
    request['offset'] = 0
    request['pageSize'] = 1000
    response = upsourceRequest(upsourceUrl, user, password, "getUsersRoles", request)
    userRoles = response.get('result').get('userRoles')
    if userRoles != None:
      for role in userRoles:
        userId = role.get('userId')
        users.append(userId)
      projectToUserIdsMap[project] = users
  return projectToUserIdsMap

def addUserToProject(upsourceUrl, user, password, project, userToAdd):
  request = {}
  request['projectId'] = project
  request['userId'] = userToAdd
  request['roleKey'] = "developer"
  response = upsourceRequest(upsourceUrl, user, password, "addUserRole", request)

def removeUserFromProject(upsourceUrl, user, password, project, userToRemove):
  # Use hub API for now since Upsource API is broken
  response = hubRequest(upsourceUrl, user, password, 'users/' + userToRemove + '/projectroles?$top=-1&fields=id,project(name),role(key)', None)
  for projectRole in response.get('projectroles'):
    if projectRole.get('project').get('name') == project and projectRole.get('role').get('key') == 'developer':
      roleId = projectRole.get('id')
      response = hubRequest(upsourceUrl, user, password, 'users/' + userToRemove + '/projectroles/' + roleId, 'DELETE')
      return
  #  request = {}
  #  request['projectId'] = project
  #  request['userId'] = userToRemove
  #  request['roleKey'] = "developer"
  #  try:
  #    response = upsourceRequest(upsourceUrl, user, password, "deleteUserRole", request)
  #  except:
  #    logit('Failed to delete user role; user=' + userToRemove + '; project=' + project)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('upsourceUrl', help='Upsource API URL')
  parser.add_argument('user', help='Upsource API user ID or email address')
  parser.add_argument('passwordFile', help='file containing the upsource API user password')
  parser.add_argument('userAccessFile', help='JSON file containing map of user to repository access rights')
  parser.add_argument('repoProjectFile', help='JSON file containing map of repository IDs to Upsource project IDs')
  parser.add_argument('vcsUrl', help='VCS SSH URL; repository names will be appended to the end of this URL')
  parser.add_argument('vcsPrivateKeyFile', help='VCS SSH Private Key File in PEM format')
  args = parser.parse_args()

  password = ""
  with open(args.passwordFile, "r") as fp:
    password = fp.read().strip()

  vcsPrivateKey = ""
  with open(args.vcsPrivateKeyFile, "r") as fp:
    vcsPrivateKey = fp.read()

  userToReposMap = {}
  with open(args.userAccessFile, "r") as fp:
    userToReposMap = json.load(fp)

  repoProjectOverrides = {}
  with open(args.repoProjectFile, "r") as fp:
    repoProjectOverrides = json.load(fp)
  
  # Sync users with Upsource, returning mapping of user email to Upsource ID
  emailToUserIdMap = syncUsersWithUpsource(args.upsourceUrl, args.user, password, userToReposMap.keys())

  # Construct a mapping of projects to allowed Upsource user IDs
  repoToUserIdsMap = constructRepoToUserIdsMap(userToReposMap, emailToUserIdMap)

  # Convert repo names to project names
  newProjectToDetailsMap = convertRepoToProject(repoToUserIdsMap, repoProjectOverrides)

  # Sync projects with Upsource, returning mapping of existing project to allowed list of user IDs.
  existingProjectToUserIdsMap = syncProjectsWithUpsource(args.upsourceUrl, args.user, password, newProjectToDetailsMap, args.vcsUrl, vcsPrivateKey)

  for project in existingProjectToUserIdsMap:
    # Remove users from projects if not declared in new mapping
    removeUsers = difference(existingProjectToUserIdsMap[project], newProjectToDetailsMap.get(project).get("users"))
    for user in removeUsers:
      removeUserFromProject(args.upsourceUrl, args.user, password, project, user)

  for project in newProjectToDetailsMap:
    # Add users to projects as declared in new mapping
    addUsers = difference(newProjectToDetailsMap.get(project).get("users"), existingProjectToUserIdsMap.get(project))
    for user in addUsers:
      addUserToProject(args.upsourceUrl, args.user, password, project, user)

if __name__ == '__main__':
  main()