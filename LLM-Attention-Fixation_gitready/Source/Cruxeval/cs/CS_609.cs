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

    public static Dictionary<long, long> F(Dictionary<long, long> array, long elem) {
        var result = new Dictionary<long, long>(array);
        while (result.Count > 0)
        {
            var lastKey = result.Keys.Last();
            var lastValue = result[lastKey];
            result.Remove(lastKey);

            if (elem == lastKey || elem == lastValue)
            {
                foreach (var kvp in array)
                {
                    if (!result.ContainsKey(kvp.Key))
                    {
                        result[kvp.Key] = kvp.Value;
                    }
                }
            }
        }
        return result;
    }
    public static void Main(string[] args) {
    Debug.Assert(Equals(F((new Dictionary<long,long>()), (1L)), (new Dictionary<long,long>())));
    }

}
