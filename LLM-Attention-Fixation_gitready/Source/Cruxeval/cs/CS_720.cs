using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(List<string> items, string item) {
        while (items.Last() == item)
        {
            items.RemoveAt(items.Count - 1);
        }
        items.Add(item);
        return items.Count;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<string>(new string[]{(string)"bfreratrrbdbzagbretaredtroefcoiqrrneaosf"})), ("n")) == (2L));
    }

}
