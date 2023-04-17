
import 'package:flutter/material.dart';

// stores ExpansionPanel state information
class StateItem {
  StateItem({
    required this.serviceState,
    required this.serviceName,
    required this.serviceUri,
  });

  bool isExpanded = false;
  int serviceState = 0;
  String serviceName = 'No Service';
  String servicePath = '点击此处配置服务路径';
  String serviceExecCmd = 'flask run';
  String serviceUrlHost = 'https://127.0.0.1';
  String serviceUri = '/service_name/get_state';

}

List<StateItem> generateStateList() {
  List<StateItem> stateItemList = [];
  var stateItemSingle = StateItem(
      serviceState: 0,
      serviceName: '织锦 FastBuild 服务',
      serviceUri: '/zhijin_compiler/get_state'
  );
  stateItemList.add(stateItemSingle);
  stateItemSingle = StateItem(
      serviceState: 1,
      serviceName: '织锦 Flask 后端服务',
      serviceUri: '/zhijin_flask/get_state'
  );
  stateItemList.add(stateItemSingle);
  stateItemSingle = StateItem(
      serviceState: 2,
      serviceName: '织锦  Vue  前端服务',
      serviceUri: '/zhijin_vue/get_state'
  );
  stateItemList.add(stateItemSingle);
  stateItemSingle = StateItem(
      serviceState: 3,
      serviceName: '织锦 Server Flutter 自动构建服务',
      serviceUri: '/zhijin_flutter_server/get_state'
  );
  stateItemList.add(stateItemSingle);
  return stateItemList;
}

class _ServersStatePageState extends State<ServersStatePage> {
  final List<StateItem> _data = generateStateList();

  @override
  Widget build(BuildContext context) {
    return Row(children: [
      Expanded(flex: 1, child: Container()),
      Expanded(
        flex: 3,
        child: SingleChildScrollView(
          child: Container(
            child: _buildPanel(),
          ),
        ),
      ),
      Expanded(flex: 1, child: Container()),
    ],);
  }

  Widget _buildPanel() {
    return ExpansionPanelList(
      expansionCallback: (int index, bool isExpanded) {
        setState(() {
          _data[index].isExpanded = !isExpanded;
        });
      },
      children: _data.map<ExpansionPanel>((StateItem item) {
        return ExpansionPanel(
          headerBuilder: (BuildContext context, bool isExpanded) {
            Color stateIconColor = Colors.yellow.shade700;
            Icon stateIcon = Icon(Icons.sync_problem, color: stateIconColor,);
            Text stateText = const Text(' - 未配置');
            if (item.serviceState == 1) {
              stateIconColor = Colors.green;
              stateText = const Text(' - 运行中');
              stateIcon = Icon(Icons.check_circle_outline, color: stateIconColor,);
            } else if (item.serviceState == 2) {
              stateIconColor = Colors.red;
              stateText = const Text(' - 未运行');
              stateIcon = Icon(Icons.cancel_outlined, color: stateIconColor,);
            } else if (item.serviceState == 3) {
              stateIconColor = Colors.grey;
              stateText = const Text(' - 检测中');
              stateIcon = Icon(Icons.sync_outlined, color: stateIconColor,);
            }
            return Row(children: [
              Container(width: 20,),
              stateIcon,
              Container(width: 20,),
              Text(item.serviceName),
              stateText,
            ],);
          },
          body: Column(children: [
            Container(height: 10,),
            Row(children: [
              Container(width: 20,),
              Text('检测服务： ${item.serviceUrlHost + item.serviceUri}'),
              Expanded(child: Container(),),
              OutlinedButton(onPressed: () {}, child: const Text('自动检测')),
              Container(width: 20,),
            ],),
            Container(height: 10,),
            Row(children: [
              Container(width: 20,),
              Text('本地路径： ${item.servicePath}'),
              Expanded(child: Container(),),
              const OutlinedButton(onPressed: null, child: Text('一键部署'),),
              Container(width: 20,),
            ],),
            Container(height: 10,),

            Container(height: 10,),
          ],),
          isExpanded: item.isExpanded,
        );
      }).toList(),
    );
  }
}

class ServersStatePage extends StatefulWidget {
  const ServersStatePage({super.key});

  @override
  State<ServersStatePage> createState() => _ServersStatePageState();
}
