using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;
class Program
{
    static int F(string text)
    {
        int a = 0;
        if (text.Substring(1).Contains(text[0]))
        {
            a += 1;
        }
        for (int i = 0; i < text.Length - 1; i++)
        {
            if (text.Substring(i + 1).Contains(text[i]))
            {
                a += 1;
            }
        }
        return a;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("3eeeeeeoopppppppw14film3oee3")) == (18L));
    }

}
