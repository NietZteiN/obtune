using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;
class Program
{
    static bool F(string sentence)
    {
        foreach (char c in sentence)
        {
            if ((int)c > 127)
            {
                return false;
            }
        }
        return true;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("1z1z1")) == (true));
    }

}
