using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, long tabsize) {
        string[] lines = text.Split('\n');
        for (int i = 0; i < lines.Length; i++)
        {
            lines[i] = lines[i].Replace("\t", new string(' ', (int)tabsize));
        }
        return string.Join("\n", lines);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("	f9\n	ldf9\n	adf9!\n	f9?"), (1L)).Equals((" f9\n ldf9\n adf9!\n f9?")));
    }

}
