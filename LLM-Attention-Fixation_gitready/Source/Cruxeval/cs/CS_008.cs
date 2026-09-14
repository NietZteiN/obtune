using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;

class Problem {
    public static string F(string str, long encryption) {
        if (encryption == 0)
        {
            return str;
        }
        else
        {
            return Rot13(str.ToUpper());
        }
    }

    public static string Rot13(string value)
    {
        char[] array = value.ToCharArray();
        for (int i = 0; i < array.Length; i++)
        {
            int number = array[i];

            if (number >= 'A' && number <= 'Z')
            {
                if (number > 'M')
                {
                    number -= 13;
                }
                else
                {
                    number += 13;
                }
            }
            array[i] = (char)number;
        }
        return new string(array);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("UppEr"), (0L)).Equals(("UppEr")));
    }

}
