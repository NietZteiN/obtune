using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(long num) {
        List<long> initial = new List<long>{1};
        List<long> total = initial;
        for (int i = 0; i < num; i++)
        {
            total = new List<long>{1}.Concat(total.Zip(total.Skip(1), (x, y) => x + y)).ToList();
            initial.Add(total.Last());
        }
        return initial.Sum();
    }
    public static void Main(string[] args) {
    Debug.Assert(F((3L)) == (4L));
    }

}
