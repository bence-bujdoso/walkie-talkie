using System;
using System.Reflection;
using System.Linq;

class GetConstants
{
    static void Main()
    {
        Assembly asm = Assembly.LoadFrom("TK11.exe");
        Type wfm = null;

        foreach (Type t in asm.GetTypes())
        {
            if (t.Name == "wfm_progress")
            {
                wfm = t;
                break;
            }
        }

        if (wfm == null)
        {
            Console.WriteLine("Class not found");
            return;
        }

        Console.WriteLine("=== CONSTANTS AND FIELDS ===\n");

        FieldInfo[] fields = wfm.GetFields(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.Instance);

        foreach (FieldInfo field in fields)
        {
            Console.WriteLine(field.Name + ":");
            Console.WriteLine("  Type: " + field.FieldType);
            Console.WriteLine("  IsStatic: " + field.IsStatic);
            Console.WriteLine("  IsLiteral: " + field.IsLiteral);

            if (field.IsStatic && field.IsLiteral)
            {
                try
                {
                    object val = field.GetRawConstantValue();
                    Console.WriteLine("  Value: " + val);
                }
                catch { }
            }
            else if (field.IsStatic && !field.IsLiteral)
            {
                try
                {
                    object val = field.GetValue(null);
                    if (val != null)
                    {
                        Console.WriteLine("  Static Value: " + val);
                    }
                }
                catch { }
            }
            Console.WriteLine();
        }
    }
}
