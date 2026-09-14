using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string s) {
        int count = 0;
        for (int i = 0; i < s.Length; i++)
        {
            if (s.LastIndexOf(s[i]) != s.IndexOf(s[i]))
            {
                count++;
            }
        }
        return count;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("abca dea ead")) == (10L));
    }

}
