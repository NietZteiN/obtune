using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string x) {
        char[] charArray = x.ToCharArray();
        Array.Reverse(charArray);
        return string.Join(" ", charArray);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("lert dna ndqmxohi3")).Equals(("3 i h o x m q d n   a n d   t r e l")));
    }

}
