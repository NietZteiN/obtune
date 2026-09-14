using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string str, List<long> numbers) {
        List<string> arr = new List<string>();
        foreach (long num in numbers)
        {
            arr.Add(str.PadLeft((int)num, '0'));
        }
        return string.Join(" ", arr);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("4327"), (new List<long>(new long[]{(long)2L, (long)8L, (long)9L, (long)2L, (long)7L, (long)1L}))).Equals(("4327 00004327 000004327 4327 0004327 4327")));
    }

}
