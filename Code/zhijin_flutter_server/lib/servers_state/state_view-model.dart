
import 'dart:convert';
import 'dart:io';
import 'dart:ffi' as ffi;
import 'package:ffi/ffi.dart';
import 'package:path/path.dart' as path;
import 'package:flutter/foundation.dart';
import 'package:dio/dio.dart';
import 'package:dio_http2_adapter/dio_http2_adapter.dart';
import 'state_model.dart';

typedef GetCosFileFromRemoteFuncFFIType = ffi.Int8 Function(
    ffi.Pointer<Utf8>,
    ffi.Pointer<Utf8>,
    ffi.Pointer<Utf8>
    );

typedef GetCosFileFromRemoteFuncType = int Function(
    ffi.Pointer<Utf8>,
    ffi.Pointer<Utf8>,
    ffi.Pointer<Utf8>
    );

typedef GetObjectFromQcloudSdkFuncFFIType = ffi.Int8 Function(
    ffi.Int8,
    ffi.Pointer<Utf8>,
    ffi.Pointer<Utf8>,
    ffi.Pointer<Utf8>,
    ffi.Pointer<Utf8>,
    ffi.Pointer<Utf8>,
    ffi.Pointer<Utf8>,
    ffi.Pointer<Utf8>
    );

typedef GetObjectFromQcloudSdkFuncType = int Function(
    int,
    ffi.Pointer<Utf8>,
    ffi.Pointer<Utf8>,
    ffi.Pointer<Utf8>,
    ffi.Pointer<Utf8>,
    ffi.Pointer<Utf8>,
    ffi.Pointer<Utf8>,
    ffi.Pointer<Utf8>
    );

class ServersStateViewModel extends ValueNotifier<ServersStateModel>{
  String checkBaseUrl;
  int timeOutSec;
  Dio clientDio = Dio();
  late GetCosFileFromRemoteFuncType getCosFileFromRemoteFunc;
  int getCosFileFromRemoteState = -1;
  late GetObjectFromQcloudSdkFuncType getObjectFromQcloudSdkFunc;
  int getObjectFromQcloudSdkFuncState = -1;

  ServersStateViewModel({
    required this.checkBaseUrl,
    this.timeOutSec = 10,
  }) : super(ServersStateModel()) {
    // Dio init
    clientDio = Dio()
      ..options.baseUrl = checkBaseUrl
      ..interceptors.add(LogInterceptor())
      ..httpClientAdapter = HttpClientAdapter();
    // library init
    String libraryPath = 'noSupported';
    if (Platform.isWindows) {
      libraryPath = path.join(Directory.current.path, 'zhijin_library',
          'Debug', 'zhijin.dll');
    } else if (Platform.isLinux) {
      libraryPath = 'noSupported';
      /*
      libraryPath = path.join(Directory.current.path, 'zhijin_library',
          'libzhijin.so');
      */
    } else if (Platform.isMacOS) {
      libraryPath = 'noSupported';
      /*
      libraryPath = path.join(Directory.current.path, 'zhijin_library',
          'libzhijin.dylib');
      */
    }
    if (libraryPath != 'noSupported') {
      final dylib = ffi.DynamicLibrary.open(libraryPath);
      getCosFileFromRemoteFunc = dylib
          .lookup<ffi.NativeFunction<GetCosFileFromRemoteFuncFFIType>>('get_cos_file_from_remote')
          .asFunction();
      getCosFileFromRemoteState = 1;
      getObjectFromQcloudSdkFunc = dylib
          .lookup<ffi.NativeFunction<GetObjectFromQcloudSdkFuncFFIType>>('get_object_from_qcloud_sdk')
          .asFunction();
      getObjectFromQcloudSdkFuncState = 1;
    } else {
      if (kDebugMode) {
        print('Platform is not supported feature "get_cos_file_from_remote"!');
        print('Platform is not supported feature "get_object_from_qcloud_sdk"!');
      }
      getCosFileFromRemoteState = 2;
      getObjectFromQcloudSdkFuncState = 2;
    }
  }

  Future<bool> check(String uri) async {
    Response<String> response;
    try {
      response = await clientDio.get(uri);
      for (final e in response.redirects) {
        if (kDebugMode) {
          print('redirect: ${e.statusCode} ${e.location}');
        }
      }
      if (kDebugMode) {
        print(response.data);
      }
      return true;
    } catch (e) {
      if (kDebugMode) {
        print('远程服务器连接失败！');
      }
      return false;
    }
  }

  List getCheckStateList() {
    return value.checkStateList;
  }

  int getInitState() {
    return value.initState;
  }

  Future<int> getCosFileFromRemoteFFI(String objectName, String localPath) async {
    if (getCosFileFromRemoteState != 1) {
      return -1;
    }
    try {
      int appId = value.remoteCosConf['appId'];
      String region = value.remoteCosConf['Region'];
      String bucketName = value.remoteCosConf['CosBucketName'];
      final federationTokenJson = await clientDio.get('/get_tencent_cos_federation_token');
      Map<String, dynamic> federationToken = jsonDecode(federationTokenJson.toString());
      if (kDebugMode) {
        print(federationTokenJson);
        print(federationToken);
      }
      String token = federationToken['Credentials']['Token'];
      String tmpSecretId = federationToken['Credentials']['TmpSecretId'];
      String tmpSecretKey = federationToken['Credentials']['TmpSecretKey'];
      if (kDebugMode) {
        print(token);
        print(tmpSecretId);
        print(tmpSecretKey);
      }
      if (kDebugMode) {
        /*
        int getState = getCosFileFromRemoteFunc(
            token.toNativeUtf8(),
            tmpSecretId.toNativeUtf8(),
            tmpSecretKey.toNativeUtf8()
        );
        print(getState);
        */
        int getState = getObjectFromQcloudSdkFunc(
            appId,
            region.toNativeUtf8(),
            bucketName.toNativeUtf8(),
            objectName.toNativeUtf8(),
            localPath.toNativeUtf8(),
            token.toNativeUtf8(),
            tmpSecretId.toNativeUtf8(),
            tmpSecretKey.toNativeUtf8()
        );
        print(getState);
      }
    }
    catch (e) {
      if (kDebugMode) {
        print('token 远程服务器连接失败！');
      }
    }
    // String resultJson = '';
    // getCosFileFromRemote();
    return -1;
  }
}
