using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        string[] words = text.Split(' ');
        foreach (string word in words) {
            if (!int.TryParse(word, out _)) {
                return "no";
            }
        }
        return "yes";
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("03625163633 d")).Equals(("no")));
    }

}
