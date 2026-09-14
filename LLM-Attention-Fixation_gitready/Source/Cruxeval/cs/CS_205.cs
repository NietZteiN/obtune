using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string a) {
        for (int i = 0; i < 10; i++)
        {
            for (int j = 0; j < a.Length; j++)
            {
                if (a[j] != '#')
                {
                    a = a.Substring(j);
                    break;
                }
            }
            if (a == "")
            {
                break;
            }
        }
        
        while (a[a.Length - 1] == '#')
        {
            a = a.Substring(0, a.Length - 1);
        }

        return a;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("##fiu##nk#he###wumun##")).Equals(("fiu##nk#he###wumun")));
    }

}
