using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string char1, string char2) {
        var t1a = new List<char>();
        var t2a = new List<char>();
        for (int i = 0; i < char1.Length; i++)
        {
            t1a.Add(char1[i]);
            t2a.Add(char2[i]);
        }
        
        var t1 = text.ToCharArray();
        for (int i = 0; i < t1.Length; i++)
        {
            int index = t1a.IndexOf(t1[i]);
            if (index != -1)
            {
                t1[i] = t2a[index];
            }
        }
        
        return new string(t1);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("ewriyat emf rwto segya"), ("tey"), ("dgo")).Equals(("gwrioad gmf rwdo sggoa")));
    }

}
