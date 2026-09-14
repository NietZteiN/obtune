using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string text, long s, long e) {
        string sublist = text.Substring((int)s, (int)(e - s));
        if (string.IsNullOrEmpty(sublist)) {
            return -1;
        }
        return sublist.IndexOf(sublist.Min());
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("happy"), (0L), (3L)) == (1L));
    }

}
