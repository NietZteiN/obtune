using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;

class Problem {
    public static bool F(string s1, string s2) {
        for (int k = 0; k < s2.Length + s1.Length; k++) {
            s1 += s1[0];
            s1 = s1.Substring(1); // Remove the first character after appending it to the end
            if (s1.IndexOf(s2) >= 0) {
                return true;
            }
        }
        return false;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("Hello"), (")")) == (false));
    }

}
