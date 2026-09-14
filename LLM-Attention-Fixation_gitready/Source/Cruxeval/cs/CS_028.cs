using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static bool F(List<long> mylist) {
        List<long> revl = new List<long>(mylist);
        revl.Reverse();
        mylist.Sort();
        mylist.Reverse();
        return Enumerable.SequenceEqual(mylist, revl);
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)5L, (long)8L}))) == (true));
    }

}
