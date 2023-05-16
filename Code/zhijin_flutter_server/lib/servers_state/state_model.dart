
import 'dart:io';
import 'dart:convert';

import 'package:flutter/foundation.dart';

// 1. TODO: Flask Auto Install
// 1.1 Tencent Cos (Python)
// 1.2 Tencent Cos (Flutter)
// 1.3 Tencent Cos (C++)
// 1.4 TODO: 7zip unzip (Flutter)
// 1.5 TODO: Auto Install Script (Flutter)
// 2. TODO: Flask Check Path

class ServersStateModel {
  String configPath = 'noSupported';
  // initState :
  // -1 : 未初始化
  //  1 : 成功初始化
  //  2 : 不支持的平台
  int initState = -1;
  String appTitle = "";
  List checkStateList = [];
  Map<String, dynamic> remoteCosConf = {};

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
    // Map<String, dynamic> globalConfigMap = configJson['checkStateModule']['globalConfig'];
    for (Map<String, dynamic> checkStateMap in configJson['checkStateModule']['checkStateList']) {
      Map<String, dynamic> checkStateNode = checkStateMap;
      checkStateNode['serviceState'] = 0;
      checkStateList.add(checkStateNode);
    }
    remoteCosConf = configJson['remoteCosModule'];
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
