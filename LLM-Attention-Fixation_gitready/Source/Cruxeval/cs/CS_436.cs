using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(string s, List<long> characters) {
        return characters.Select(i => s.Substring((int)i, 1)).ToList();
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("s7 6s 1ss"), (new List<long>(new long[]{(long)1L, (long)3L, (long)6L, (long)1L, (long)2L}))).SequenceEqual((new List<string>(new string[]{(string)"7", (string)"6", (string)"1", (string)"7", (string)" "}))));
    }

}
