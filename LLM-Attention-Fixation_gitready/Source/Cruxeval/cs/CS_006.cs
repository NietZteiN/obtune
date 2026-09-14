using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<Tuple<string, long>> F(Dictionary<string,long> dic) {
        var sortedDic = dic.OrderBy(x => x.Key.Length).ToList();
        for(int i = 0; i < sortedDic.Count - 1; i++)
        {
            dic.Remove(sortedDic[i].Key);
        }
        return dic.Select(x => Tuple.Create(x.Key, x.Value)).ToList();
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new Dictionary<string,long>(){{"11", 52L}, {"65", 34L}, {"a", 12L}, {"4", 52L}, {"74", 31L}})).SequenceEqual((new List<Tuple<string, long>>(new Tuple<string, long>[]{(Tuple<string, long>)Tuple.Create("74", 31L)}))));
    }

}
