
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:beamer/beamer.dart';
// import 'package:webf_websocket/webf_websocket.dart';
import 'color_schemes.g.dart';
import 'servers_state/state_view.dart';
import 'tasks_manage/tasks_manage_view.dart';
// import 'code_editor/editor_gui.dart';

bool schemeFlags = false;

void reserveSchemeFlags() {
  if (schemeFlags) {
    schemeFlags = false;
  } else {
    schemeFlags = true;
  }
}

class _GlobalScaffoldState extends State<GlobalScaffold> {
  String schemeMode = '夜间模式';

  Drawer sidebarDrawer() {
    if (schemeFlags) {
      schemeMode = '日间模式';
    } else {
      schemeMode = '夜间模式';
    }
    return Drawer(
      child: ListView(
        padding: EdgeInsets.zero,
        children: <Widget>[
          DrawerHeader(
            child: Center(child: Text(
              '织锦',
              style: Theme.of(context).textTheme.titleMedium,
            ),),
          ),
          ListTile(
            leading: const Icon(Icons.home),
            title: const Text('主页'),
            onTap: () {
              Beamer.of(context).beamToNamed('/index');
            },
          ),
          ListTile(
            leading: const Icon(Icons.view_timeline),
            title: const Text('服务器状态'),
            onTap: () {
              Beamer.of(context).beamToNamed('/servers_state');
            },
          ),
          ListTile(
            leading: const Icon(Icons.format_list_numbered),
            title: const Text('任务管理'),
            onTap: () {
              Beamer.of(context).beamToNamed('/tasks_manage');
            },
          ),
          const ListTile(
            leading: Icon(Icons.edit_note),
            title: Text('项目编辑器'),
            /*onTap: () {
              Beamer.of(context).beamToNamed('/code_editor');
            },*/
          ),
          ListTile(
            leading: const Icon(Icons.dark_mode),
            title: Text(schemeMode),
            onTap: () {
              setState(() {
                reserveSchemeFlags();
              });
            },
          ),
          ListTile(
            leading: const Icon(Icons.info),
            title: const Text('关于'),
            onTap: () {
              Beamer.of(context).beamToNamed('/index');
            },
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        appBar: AppBar(),
        drawer: sidebarDrawer(),
        body: widget.childPage,
    );
  }
}

class GlobalScaffold extends StatefulWidget {
  const GlobalScaffold({super.key, required this.childPage});
  final Widget childPage;

  @override
  State<GlobalScaffold> createState() => _GlobalScaffoldState();
}

class _MainPageState extends State<MainPage> {
  @override
  Widget build(BuildContext context) {
    return Column(children: [
      Expanded(flex: 2, child: Container(),),
      Expanded(flex: 1, child: Center(child: Text(
        '织锦服务端开发工具',
        style: Theme.of(context).textTheme.titleLarge,
      ),),),
      Expanded(flex: 1, child: Center(
        child: FilledButton(
          child: const Text('开始使用'),
          onPressed: () {
            Beamer.of(context).beamToNamed('/servers_state');
          },
        ),
      ),),
      Expanded(flex: 2, child: Container(),),
    ],);
  }
}

class MainPage extends StatefulWidget {
  const MainPage({super.key});

  @override
  State<MainPage> createState() => _MainPageState();
}

class MyApp extends StatelessWidget {
  MyApp({super.key});

  final routerDelegate = BeamerDelegate(
    locationBuilder: RoutesLocationBuilder(
      routes: {
        '/': (context, state, data) => const GlobalScaffold(
            childPage: MainPage()
        ),
        '/index': (context, state, data) => const GlobalScaffold(
            childPage: MainPage()
        ),
        '/servers_state': (context, state, data) => const GlobalScaffold(
            childPage: ServersStatePage()
        ),
        '/tasks_manage': (context, state, data) => const GlobalScaffold(
            childPage: TasksManagePage()
        ),
        '/code_editor': (context, state, data) => const GlobalScaffold(
            childPage: MainPage()
        ),
      },
    ),
  );

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      localizationsDelegates: const [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [
        Locale.fromSubtags(
            languageCode: 'zh', scriptCode: 'Hans', countryCode: 'CN'),
        // Chinese *See Advanced Locales below*
      ],
      title: '织锦服务端开发工具',
      theme: ThemeData(useMaterial3: true, colorScheme: lightColorScheme),
      darkTheme: ThemeData(useMaterial3: true, colorScheme: darkColorScheme),
      routeInformationParser: BeamerParser(),
      routerDelegate: routerDelegate,
    );
  }
}

void main() {
  // WebFWebSocket.initialize();
  runApp(MyApp());
}
