using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string haystack, string needle) {
        for (int i = haystack.IndexOf(needle); i >= 0; i--)
        {
            if (haystack.Substring(i) == needle)
            {
                return i;
            }
        }
        return -1;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("345gerghjehg"), ("345")) == (-1L));
    }

}
