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

    public static Dictionary<string, long> F(Dictionary<string, long> obj) {
        var keys = obj.Keys.ToList();
        foreach (var k in keys)
        {
            if (obj[k] >= 0)
            {
                obj[k] = -obj[k];
            }
        }
        return obj;
    }
    public static void Main(string[] args) {
    Debug.Assert(Equals(F((new Dictionary<string,long>(){{"R", 0L}, {"T", 3L}, {"F", -6L}, {"K", 0L}})), (new Dictionary<string,long>(){{"R", 0L}, {"T", -3L}, {"F", -6L}, {"K", 0L}})));
    }

}
