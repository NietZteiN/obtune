using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static bool F(string x) {
        int n = x.Length;
        int i = 0;
        while (i < n && char.IsDigit(x[i]))
        {
            i++;
        }
        return i == n;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("1")) == (true));
    }

}
