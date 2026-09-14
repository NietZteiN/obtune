using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string s, string ch) {
        if (!s.Contains(ch)) {
            return "";
        }
        s = s.Substring(s.IndexOf(ch) + 1);
        char[] charArray = s.ToCharArray();
        Array.Reverse(charArray);
        s = new string(charArray);
        for (int i = 0; i < s.Length; i++) {
            s = s.Substring(s.IndexOf(ch) + 1);
            charArray = s.ToCharArray();
            Array.Reverse(charArray);
            s = new string(charArray);
        }
        return s;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("shivajimonto6"), ("6")).Equals(("")));
    }

}
