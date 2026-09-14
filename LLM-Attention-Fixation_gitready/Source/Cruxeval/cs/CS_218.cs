using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string str, string sep) {
        int cnt = RepeatCounter(str, sep);
        string new_str = "";
        for (int i=0; i<cnt; i++)
        {
            new_str += str + sep;
        }
        char[] charArray = new_str.ToCharArray();
        Array.Reverse(charArray);
        return new string(charArray);
    }
    
    public static int RepeatCounter(string str, string sep)
    {
        int count = 0, minIndex = str.IndexOf(sep);
        while (minIndex != -1)
        {
            count++;
            minIndex = str.IndexOf(sep, minIndex + sep.Length);
        }
        return count;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("caabcfcabfc"), ("ab")).Equals(("bacfbacfcbaacbacfbacfcbaac")));
    }

}
