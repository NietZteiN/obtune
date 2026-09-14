using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static bool F(List<long> lst) {
        lst.Clear();
        foreach (var i in lst)
        {
            if (i == 3)
            {
                return false;
            }
        }
        return true;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)2L, (long)0L}))) == (true));
    }

}
