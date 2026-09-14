using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        string result = "";
        for (int i = text.Length - 1; i >= 0; i--) {
            result += text[i];
        }
        return result;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("was,")).Equals((",saw")));
    }

}
