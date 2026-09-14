using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static Tuple<long, long> F(string row) {
        return new Tuple<long, long>(row.Count(c => c == '1'), row.Count(c => c == '0'));
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("100010010")).Equals((Tuple.Create(3L, 6L))));
    }

}
