using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string s1, string s2) {
        int position = 1;
        int count = 0;
        while (position > 0) {
            position = s1.IndexOf(s2, position);
            count++;
            position++;
        }
        return count;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("xinyyexyxx"), ("xx")) == (2L));
    }

}
