using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        var a = text.Split('\n');
        var b = new List<string>();
        for (int i = 0; i < a.Length; i++)
        {
            var c = a[i].Replace("\t", "    ");
            b.Add(c);
        }
        return string.Join("\n", b);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("			tab tab tabulates")).Equals(("            tab tab tabulates")));
    }

}
