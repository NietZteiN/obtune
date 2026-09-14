using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string n) {
        foreach (char i in n)
        {
            if (!char.IsDigit(i))
            {
                return -1;
            }
        }
        return int.Parse(n);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("6 ** 2")) == (-1L));
    }

}
