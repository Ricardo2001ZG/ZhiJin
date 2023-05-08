
import 'dart:io';
import 'dart:convert';

import 'package:flutter/foundation.dart';

// 1. TODO: Flask Check Path
// 2. TODO: Flask Auto Install

Map<String, dynamic> getStateItem({
  required String serviceName,
  required String serviceUrlHost,
  required String serviceUri,
  String servicePath = '点击此处配置服务路径',
  String serviceExecCmd = 'flask run',
}) {
  Map<String, dynamic> stateItemNode = {};
  // stateItemNode['serviceName'] = 'No Service';
  stateItemNode['serviceName'] = serviceName;
  // stateItemNode['serviceUrlHost'] = 'https://127.0.0.1';
  stateItemNode['serviceUrlHost'] = serviceUrlHost;
  // stateItemNode['serviceUri'] = '/service_name/get_state';
  stateItemNode['serviceUri'] = serviceUri;
  stateItemNode['servicePath'] = servicePath;
  stateItemNode['serviceExecCmd'] = serviceExecCmd;
  stateItemNode['firstAutoCheck'] = false;
  stateItemNode['serviceState'] = 0;
  return stateItemNode;
}

class ServersStateModel {
  String configPath = 'noSupported';
  // initState :
  // -1 : 未初始化
  //  1 : 成功初始化
  //  2 : 不支持的平台
  int initState = -1;
  String appTitle = "";
  List checkStateList = [];

  Future<File> get _localFileAsync async {
    return File(configPath);
  }

  File get _localFile {
    return File(configPath);
  }

  Future<File> writeConfig(String configJson) async {
    final file = await _localFileAsync;
    return file.writeAsString(configJson);
  }

  void writeDataFromJson(Map<String, dynamic> configJson) {
    appTitle = configJson['appTitle'];
    Map<String, dynamic> globalConfigMap = configJson['checkStateModule']['globalConfig'];
    for (Map<String, dynamic> checkStateMap in configJson['checkStateModule']['checkStateList']) {
      Map<String, dynamic> checkStateNode = getStateItem(
          serviceName: checkStateMap['serviceName'],
          serviceUrlHost: checkStateMap['serviceHost'],
          serviceUri: checkStateMap['serviceUri']
      );
      checkStateList.add(checkStateNode);
    }
    if (kDebugMode) {
      print(checkStateList.toString());
    }
  }

  ServersStateModel() {
    if (Platform.isWindows) {
      configPath = 'zhijin_config.json';
    } else {
      configPath = 'noSupported';
    }
    if (configPath == 'noSupported') {
      initState = 2;
    } else {
      try {
        final configFile = _localFile;
        String configString = configFile.readAsStringSync(encoding: utf8);
        writeDataFromJson(jsonDecode(configString));
        initState = 1;
      } catch (e) {
        if (kDebugMode) {
          print('Load configFile failed!');
          print(e.toString());
        }
      }
    }
  }
}
