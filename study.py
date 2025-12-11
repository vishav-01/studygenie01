import 'package:flutter/material.dart';

void main() {
  runApp(StudyGenieApp());
}

class StudyGenieApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: "StudyGenie",
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.light,
        primaryColor: DoraemonColors.skyBlue,
        colorScheme: ColorScheme.fromSeed(
          seedColor: DoraemonColors.skyBlue,
        ),
      ),
      darkTheme: ThemeData(
        brightness: Brightness.dark,
        primaryColor: DoraemonColors.skyBlue,
        colorScheme: ColorScheme.fromSeed(
          seedColor: DoraemonColors.skyBlue,
          brightness: Brightness.dark,
        ),
      ),
      themeMode: ThemeMode.system,
      home: HomePage(),
    );
  }
}import 'package:flutter/material.dart';

class DoraemonColors {
  // DEFAULT
  static const Color skyBlue = Color(0xFF6EC9F5);

  // FULL COLOR PALETTE
  static const Color darkBlue = Color(0xFF0096D1);
  static const Color lightBlue = Color(0xFFAEE7FF);
  static const Color yellow = Color(0xFFF7D32D);
  static const Color red = Color(0xFFE8404C);
  static const Color white = Colors.white;

  // GRADIENT (DEFAULT)
  static const LinearGradient skyBlueGradient = LinearGradient(
    colors: [
      Color(0xFF6EC9F5),
      Color(0xFF0096D1),
    ],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
}