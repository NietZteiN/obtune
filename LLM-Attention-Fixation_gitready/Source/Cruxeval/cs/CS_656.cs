using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(List<string> letters) {
        var a = new List<string>();
        foreach (var letter in letters)
        {
            if (a.Contains(letter))
            {
                return "no";
            }
            a.Add(letter);
        }
        return "yes";
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<string>(new string[]{(string)"b", (string)"i", (string)"r", (string)"o", (string)"s", (string)"j", (string)"v", (string)"p"}))).Equals(("yes")));
    }

}
