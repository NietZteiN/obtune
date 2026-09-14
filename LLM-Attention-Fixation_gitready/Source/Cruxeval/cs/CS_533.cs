using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string query, Dictionary<string,long> numBase) {
        long net_sum = 0;
        foreach (var pair in numBase)
        {
            string key = pair.Key;
            long val = pair.Value;
            if (key[0] == query[0] && key.Length == 3)
            {
                net_sum -= val;
            }
            else if (key[key.Length - 1] == query[0] && key.Length == 3)
            {
                net_sum += val;
            }
        }
        return net_sum;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("a"), (new Dictionary<string,long>())) == (0L));
    }

}
