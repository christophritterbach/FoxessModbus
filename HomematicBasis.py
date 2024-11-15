import base64
import requests
import xml.etree.ElementTree as ET

class HomematicBasis:
    def __init__(self, address, port, user, password):
        self._address = address
        self._port = port
        userpassword = user + ':' + password
        self._auth_header='Basic ' + base64.b64encode(userpassword.encode('ascii')).decode('ascii')

    def _handleRequest(self, hmip_object, function_call):
        if hmip_object in ['ID_DEVICES'] or isinstance(hmip_object, int):
            object_name = hmip_object
        else:
            object_name = '"' + hmip_object + '"'
        anfrage='http://{0}:{1}/HM.exe?Status=dom.GetObject({2}).{3}'.format(self._address, self._port, object_name, function_call)
        response=requests.get(anfrage, headers ={'Authorization': self._auth_header })
        #print(response.text)
        answer_xml = ET.fromstring(response.text)
        resp = answer_xml.findall('Status')
        return resp[0].text

    def getAllDevicesById(self):
        resp = self._handleRequest('ID_DEVICES', 'EnumUsedIDs()').split('\t')
        return resp

    def getAllDevicesByName(self):
        resp = self._handleRequest('ID_DEVICES', 'EnumUsedNames()').split('\t')
        return resp

    # OT_OBJECT
    def getObjectId(self, hmip_object):
        return self._handleRequest(hmip_object, 'ID()')

    def getObjectName(self, hmip_object):
        return self._handleRequest(hmip_object, 'Name()')

    def getObjectType(self, hmip_object):
        return self._handleRequest(hmip_object, 'Type()')

    def getObjectTypeName(self, hmip_object):
        return self._handleRequest(hmip_object, 'TypeName()')

    def getObjectState(self, hmip_object):
        return self._handleRequest(hmip_object, 'State()')

    # OT_DEVICE
    def getDeviceId(self, hmip_object):
        return self.getObjectId(hmip_object)

    def getDeviceName(self, hmip_object):
        return self.getObjectName(hmip_object)

    def getDeviceType(self, hmip_object):
        return self.getObjectType(hmip_object)

    def getDeviceTypeName(self, hmip_object):
        return self.getObjectTypeName(hmip_object)

    def getDeviceState(self, hmip_object):
        return self.getObjectState(hmip_object)

    def getDeviceChannels(self, hmip_object):
        return self._handleRequest(hmip_object, 'Channels()').split('\t')

    def getDeviceInterface(self, hmip_object):
        return self._handleRequest(hmip_object, 'Interface()')

    def getDeviceAddress(self, hmip_object):
        return self._handleRequest(hmip_object, 'Address()')

    def getDeviceHssType(self, hmip_object):
        return self._handleRequest(hmip_object, 'HssType()')

    # OT_CHANNEL
    def getChannelId(self, hmip_object):
        return self.getObjectId(hmip_object)

    def getChannelName(self, hmip_object):
        return self.getObjectName(hmip_object)

    def getChannelType(self, hmip_object):
        return self.getObjectType(hmip_object)

    def getChannelTypeName(self, hmip_object):
        return self.getObjectTypeName(hmip_object)

    def getChannelState(self, hmip_object):
        return self.getObjectState(hmip_object)

    def getChannelDevice(self, hmip_object):
        return self._handleRequest(hmip_object, 'Device()')

    def getChannelDPs(self, hmip_object):
        return self._handleRequest(hmip_object, 'DPs()').split('\t')

    def getChannelInterface(self, hmip_object):
        return self._handleRequest(hmip_object, 'Interface()')

    def getChannelAddress(self, hmip_object):
        return self._handleRequest(hmip_object, 'Address()')

    def getChannelChnGroupPartnerId(self, hmip_object):
        return self._handleRequest(hmip_object, 'ChnGroupPartnerId()')

    def getChannelChnDirection(self, hmip_object):
        return self._handleRequest(hmip_object, 'ChnDirection()')

    def getChannelChnAESActive(self, hmip_object):
        return self._handleRequest(hmip_object, 'ChnAESActive()')

    def getChannelChnRoom(self, hmip_object):
        return self._handleRequest(hmip_object, 'ChnRoom()')

    def getChannelChnFunction(self, hmip_object):
        return self._handleRequest(hmip_object, 'ChnFunction()')

    def getChannelDPByHssDP(self, hmip_object, name):
        return self._handleRequest(hmip_object, 'DPByHssDP({0})'.format(name))

    # OT_DP
    def getDPId(self, hmip_object):
        return self.getObjectId(hmip_object)

    def getDPName(self, hmip_object):
        return self.getObjectName(hmip_object)

    def getDPType(self, hmip_object):
        return self.getObjectType(hmip_object)

    def getDPTypeName(self, hmip_object):
        return self.getObjectTypeName(hmip_object)

    def getDPState(self, hmip_object):
        return self.getObjectState(hmip_object)

    def getDPValueType(self, hmip_object):
        return self._handleRequest(hmip_object, 'ValueType()')

    def getDPChannel(self, hmip_object):
        return self._handleRequest(hmip_object, 'Channel()')

    def getDPValue(self, hmip_object):
        return self._handleRequest(hmip_object, 'Value()')

    def getDPLastValue(self, hmip_object):
        return self._handleRequest(hmip_object, 'LastValue()')

    def getDPOperations(self, hmip_object):
        return self._handleRequest(hmip_object, 'Operations()')

    def getDPTimestamp(self, hmip_object):
        return self._handleRequest(hmip_object, 'Timestamp()')

    # OT_VARDP
    def getVarDPId(self, hmip_object):
        return self.getObjectId(hmip_object)

    def getVarDPName(self, hmip_object):
        return self.getObjectName(hmip_object)

    def getVarDPType(self, hmip_object):
        return self.getObjectType(hmip_object)

    def getVarDPTypeName(self, hmip_object):
        return self.getObjectTypeName(hmip_object)

    def getVarDPState(self, hmip_object):
        return self.getObjectState(hmip_object)

    def getVarDPValueType(self, hmip_object):
        return self._handleRequest(hmip_object, 'ValueType()')
    
    def getVarDPChannel(self, hmip_object):
        return self._handleRequest(hmip_object, 'Channel()')

    def getVarDPValue(self, hmip_object):
        return self._handleRequest(hmip_object, 'Value()')

    def getVarDPLastValue(self, hmip_object):
        return self._handleRequest(hmip_object, 'LastValue()')

    def getVarDPOperations(self, hmip_object):
        return self._handleRequest(hmip_object, 'Operations()')

    def getVarDPTimestamp(self, hmip_object):
        return self._handleRequest(hmip_object, 'Timestamp()')

    def getVarDPVariable(self, hmip_object):
        return self._handleRequest(hmip_object, 'Variable()')


if __name__ == '__main__':
    homematicBasis = HomematicBasis ('localhost', 8181, 'user', 'password')
    print('All by ID'   , homematicBasis.getAllDevicesById())
    print('All by Names', homematicBasis.getAllDevicesByName())
    was = 'Strom_Aktuell'
    print('Variable', was)
    print(' Name'      , homematicBasis.getVarDPName(was))
    print(' Id'        , homematicBasis.getVarDPId(was))
    print(' Type'      , homematicBasis.getVarDPType(was))
    print(' TypeName'  , homematicBasis.getVarDPTypeName(was))
    print(' State'     , homematicBasis.getVarDPState(was))
    print(' ValueType' , homematicBasis.getVarDPValueType(was))
    print(' Channel'   , homematicBasis.getVarDPChannel(was))
    print(' Value'     , homematicBasis.getVarDPValue(was))
    print(' LastValue' , homematicBasis.getVarDPLastValue(was))
    print(' Operations', homematicBasis.getVarDPOperations(was))
    print(' Timestamp' , homematicBasis.getVarDPTimestamp(was))
    print(' Variable'  , homematicBasis.getVarDPVariable(was))
    was='Garagentor Stellung'
    print(was)
    print(' Name'     , homematicBasis.getDeviceName(was))
    print(' Id'       , homematicBasis.getDeviceId(was))
    print(' Type'     , homematicBasis.getDeviceType(was))
    print(' TypeName' , homematicBasis.getDeviceTypeName(was))
    print(' State'    , homematicBasis.getDeviceState(was))
    print(' Channels' , homematicBasis.getDeviceChannels(was))
    print(' Interface', homematicBasis.getDeviceInterface(was))
    print(' Address'  , homematicBasis.getDeviceAddress(was))
    print(' HssType'  , homematicBasis.getDeviceHssType(was))
    was=2077 #DEVICE
    print('Device', was)
    print(' Name'     , homematicBasis.getDeviceName(was))
    print(' Id'       , homematicBasis.getDeviceId(was))
    print(' Type'     , homematicBasis.getDeviceType(was))
    print(' TypeName' , homematicBasis.getDeviceTypeName(was))
    print(' State'    , homematicBasis.getDeviceState(was))
    print(' Channels' , homematicBasis.getDeviceChannels(was))
    print(' Interface', homematicBasis.getDeviceInterface(was))
    print(' Address'  , homematicBasis.getDeviceAddress(was))
    print(' HssType'  , homematicBasis.getDeviceHssType(was))
    was=2112 # CHANNEL
    print('Channel', was)
    print(' Name'             , homematicBasis.getChannelName(was))
    print(' Id'               , homematicBasis.getChannelId(was))
    print(' Type'             , homematicBasis.getChannelType(was))
    print(' TypeName'         , homematicBasis.getChannelTypeName(was))
    print(' State'            , homematicBasis.getChannelState(was))
    print(' Device'           , homematicBasis.getChannelDevice(was))
    print(' DPs'              , homematicBasis.getChannelDPs(was))
    print(' Interface'        , homematicBasis.getChannelInterface(was))
    print(' Address'          , homematicBasis.getChannelAddress(was))
    print(' ChnGroupPartnerId', homematicBasis.getChannelChnGroupPartnerId(was))
    print(' ChnDirection'     , homematicBasis.getChannelChnDirection(was))
    print(' ChnAESActive'     , homematicBasis.getChannelChnAESActive(was))
    print(' ChnRoom'          , homematicBasis.getChannelChnRoom(was))
    print(' ChnFunction'      , homematicBasis.getChannelChnFunction(was))
    #print(' DPByHssDP'        , homematicBasis.getChannelDPByHssDP(was, name))
    was=2113 #DP
    print('DP', was)
    print(' Name'      , homematicBasis.getDPName(was))
    print(' Id'        , homematicBasis.getDPId(was))
    print(' Type'      , homematicBasis.getDPType(was))
    print(' TypeName'  , homematicBasis.getDPTypeName(was))
    print(' State'     , homematicBasis.getDPState(was))
    print(' ValueType' , homematicBasis.getDPValueType(was))
    print(' Channel'   , homematicBasis.getDPChannel(was))
    print(' Value'     , homematicBasis.getDPValue(was))
    print(' LastValue' , homematicBasis.getDPLastValue(was))
    print(' Operations', homematicBasis.getDPOperations(was))
    print(' Timestamp' , homematicBasis.getDPTimestamp(was))
    was=2114 #DP
    print('DP', was)
    print(' Name'      , homematicBasis.getDPName(was))
    print(' Id'        , homematicBasis.getDPId(was))
    print(' Type'      , homematicBasis.getDPType(was))
    print(' TypeName'  , homematicBasis.getDPTypeName(was))
    print(' State'     , homematicBasis.getDPState(was))
    print(' ValueType' , homematicBasis.getDPValueType(was))
    print(' Channel'   , homematicBasis.getDPChannel(was))
    print(' Value'     , homematicBasis.getDPValue(was))
    print(' LastValue' , homematicBasis.getDPLastValue(was))
    print(' Operations', homematicBasis.getDPOperations(was))
    print(' Timestamp' , homematicBasis.getDPTimestamp(was))
    was=2115 #DP
    print('DP', was)
    print(' Name'      , homematicBasis.getDPName(was))
    print(' Id'        , homematicBasis.getDPId(was))
    print(' Type'      , homematicBasis.getDPType(was))
    print(' TypeName'  , homematicBasis.getDPTypeName(was))
    print(' State'     , homematicBasis.getDPState(was))
    print(' ValueType' , homematicBasis.getDPValueType(was))
    print(' Channel'   , homematicBasis.getDPChannel(was))
    print(' Value'     , homematicBasis.getDPValue(was))
    print(' LastValue' , homematicBasis.getDPLastValue(was))
    print(' Operations', homematicBasis.getDPOperations(was))
    print(' Timestamp' , homematicBasis.getDPTimestamp(was))
    was=2116 #DP
    print('DP', was)
    print(' Name'      , homematicBasis.getDPName(was))
    print(' Id'        , homematicBasis.getDPId(was))
    print(' Type'      , homematicBasis.getDPType(was))
    print(' TypeName'  , homematicBasis.getDPTypeName(was))
    print(' State'     , homematicBasis.getDPState(was))
    print(' ValueType' , homematicBasis.getDPValueType(was))
    print(' Channel'   , homematicBasis.getDPChannel(was))
    print(' Value'     , homematicBasis.getDPValue(was))
    print(' LastValue' , homematicBasis.getDPLastValue(was))
    print(' Operations', homematicBasis.getDPOperations(was))
    print(' Timestamp' , homematicBasis.getDPTimestamp(was))
    was=2117 #DP
    print('DP', was)
    print(' Name'      , homematicBasis.getDPName(was))
    print(' Id'        , homematicBasis.getDPId(was))
    print(' Type'      , homematicBasis.getDPType(was))
    print(' TypeName'  , homematicBasis.getDPTypeName(was))
    print(' State'     , homematicBasis.getDPState(was))
    print(' ValueType' , homematicBasis.getDPValueType(was))
    print(' Channel'   , homematicBasis.getDPChannel(was))
    print(' Value'     , homematicBasis.getDPValue(was))
    print(' LastValue' , homematicBasis.getDPLastValue(was))
    print(' Operations', homematicBasis.getDPOperations(was))
    print(' Timestamp' , homematicBasis.getDPTimestamp(was))
    was='Wohnzimmer'
    print('Room', was)
    print(' Name', homematicBasis.getObjectName(was))
    print(' Id', homematicBasis.getObjectId(was))
    print(' Type', homematicBasis.getObjectType(was))
    print(' TypeName', homematicBasis.getObjectTypeName(was))
    was='FritzBox'
    print('Gewerk', was)
    print(' Name', homematicBasis.getObjectName(was))
    print(' Id', homematicBasis.getObjectId(was))
    print(' Type', homematicBasis.getObjectType(was))
    print(' TypeName', homematicBasis.getObjectTypeName(was))

