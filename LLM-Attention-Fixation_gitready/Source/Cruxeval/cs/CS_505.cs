using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string str) {
        while (!string.IsNullOrEmpty(str)) {
            if (char.IsLetter(str[str.Length - 1])) {
                return str;
            }
            str = str.Substring(0, str.Length - 1);
        }
        return str;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("--4/0-209")).Equals(("")));
    }

}
