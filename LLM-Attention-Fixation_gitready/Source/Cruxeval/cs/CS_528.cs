using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string s) {
        string b = "";
        string c = "";
        foreach (char i in s)
        {
            c = c + i;
            if (s.LastIndexOf(c) > -1)
            {
                return s.LastIndexOf(c);
            }
        }
        return 0;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("papeluchis")) == (2L));
    }

}
