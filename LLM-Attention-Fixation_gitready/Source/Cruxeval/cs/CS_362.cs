using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        for (int i = 0; i < text.Length - 1; i++) {
            if (text.Substring(i).All(char.IsLower)) {
                return text.Substring(i + 1);
            }
        }
        return "";
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("wrazugizoernmgzu")).Equals(("razugizoernmgzu")));
    }

}
