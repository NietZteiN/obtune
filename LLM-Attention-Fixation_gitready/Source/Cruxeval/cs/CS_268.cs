using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string s, string separator) {
        for (int i = 0; i < s.Length; i++)
        {
            if (s[i] == separator[0]) // Assuming the separator string has length 1
            {
                char[] newS = s.ToCharArray();
                newS[i] = '/';
                return string.Join(" ", newS);
            }
        }
        return null; // Handle case when separator is not found
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("h grateful k"), (" ")).Equals(("h / g r a t e f u l   k")));
    }

}
