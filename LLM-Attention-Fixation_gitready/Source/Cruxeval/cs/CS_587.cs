using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;

class Problem {
    public static bool Equals<TKey, TValue>(Dictionary<TKey, TValue> dict1, Dictionary<TKey, TValue> dict2)
    {
        var dict3 = dict2.Where(x => !dict1.ContainsKey(x.Key) || !EqualityComparer<TValue>.Default.Equals(dict1[x.Key], x.Value))
                         .Union(dict1.Where(x => !dict2.ContainsKey(x.Key) || !EqualityComparer<TValue>.Default.Equals(dict2[x.Key], x.Value)))
                         .ToDictionary(x => x.Key, x => x.Value);
        return dict3.Count == 0;
    }

    public static Dictionary<long, string> F(List<long> nums, string fill) {
        var ans = nums.Distinct().ToDictionary(num => num, num => fill);
        return ans;
    }
    public static void Main(string[] args) {
    Debug.Assert(Equals(F((new List<long>(new long[]{(long)0L, (long)1L, (long)1L, (long)2L})), ("abcca")), (new Dictionary<long,string>(){{0L, "abcca"}, {1L, "abcca"}, {2L, "abcca"}})));
    }

}
