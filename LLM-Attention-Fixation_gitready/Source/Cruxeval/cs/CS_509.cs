using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(long value, long width) {
        if (value >= 0)
        {
            return value.ToString().PadLeft((int)width, '0');
        }
        else
        {
            return '-' + Math.Abs(value).ToString().PadLeft((int)width - 1, '0');
        }
    }
    public static void Main(string[] args) {
    Debug.Assert(F((5L), (1L)).Equals(("5")));
    }

}
