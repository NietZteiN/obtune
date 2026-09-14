using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        foreach (char punct in "!.?,:;")
        {
            if (text.Count(x => x == punct) > 1)
            {
                return "no";
            }
            if (text.EndsWith(punct.ToString()))
            {
                return "no";
            }
        }
        return char.ToUpper(text[0]) + text.Substring(1).ToLower();
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("djhasghasgdha")).Equals(("Djhasghasgdha")));
    }

}
