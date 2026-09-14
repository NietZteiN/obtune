using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string code) {
        var lines = code.Split(']');
        var result = new List<string>();
        var level = 0;
        foreach (var line in lines)
        {
            result.Add(line[0] + " " + new string(' ', 2 * level) + line.Substring(1));
            level += line.Count(c => c == '{') - line.Count(c => c == '}');
        }
        return string.Join("\n", result);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("if (x) {y = 1;} else {z = 1;}")).Equals(("i f (x) {y = 1;} else {z = 1;}")));
    }

}
