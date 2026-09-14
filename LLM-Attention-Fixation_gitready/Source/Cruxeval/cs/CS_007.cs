using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> list) {
        List<long> original = new List<long>(list);
        while (list.Count > 1)
        {
            list.RemoveAt(list.Count - 1);
            for (int i = 0; i < list.Count; i++)
            {
                list.RemoveAt(i);
            }
        }
        list = new List<long>(original);
        if (list.Count > 0)
        {
            list.RemoveAt(0);
        }
        return list;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>())).SequenceEqual((new List<long>())));
    }

}
