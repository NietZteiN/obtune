using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string ch) {
        var result = new List<string>();
        foreach (var line in text.Split(new[] { "\r\n", "\r", "\n" }, StringSplitOptions.None)) {
            if (line.Length > 0 && line[0] == ch[0]) {
                result.Add(line.ToLower());
            } else {
                result.Add(line.ToUpper());
            }
        }
        return string.Join("\n", result);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("t\nza\na"), ("t")).Equals(("t\nZA\nA")));
    }

}
