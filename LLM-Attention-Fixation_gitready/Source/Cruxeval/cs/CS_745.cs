using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string address) {
        int suffix_start = address.IndexOf('@') + 1;
        if (address.Substring(suffix_start).Count(c => c == '.') > 1)
        {
            address = address.Remove(suffix_start + address.Split('@')[1].Split('.').Take(2).Select(s => s.Length).Sum());
        }
        return address;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("minimc@minimc.io")).Equals(("minimc@minimc.io")));
    }

}
