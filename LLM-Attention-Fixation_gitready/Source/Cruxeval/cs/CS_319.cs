using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string needle, string haystack) {
        long count = 0;
        while (haystack.Contains(needle))
        {
            haystack = haystack.Remove(haystack.IndexOf(needle), needle.Length);
            count += 1;
        }
        return count;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("a"), ("xxxaaxaaxx")) == (4L));
    }

}
