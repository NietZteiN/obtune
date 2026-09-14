using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static Tuple<long, long> F(Dictionary<string,long> marks) {
        long highest = 0;
        long lowest = 100;
        foreach (var value in marks.Values)
        {
            if (value > highest)
            {
                highest = value;
            }
            if (value < lowest)
            {
                lowest = value;
            }
        }
        return Tuple.Create(highest, lowest);
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new Dictionary<string,long>(){{"x", 67L}, {"v", 89L}, {"", 4L}, {"alij", 11L}, {"kgfsd", 72L}, {"yafby", 83L}})).Equals((Tuple.Create(89L, 4L))));
    }

}
