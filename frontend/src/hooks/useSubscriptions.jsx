import { useCallback, useEffect, useMemo, useState } from "react";
import {
  crearSuscripcion,
  convertirAMoneda,
  desactivarSuscripcion,
  listarSuscripciones,
} from "../services/Subscripciones.service";

export const initialForm = {
  id: null,
  name: "",
  amount: "",
  currency: "USD",
  frequency: "Mensual",
  billingDay: "1",
  isActive: true,
};

export function useSubscriptions() {
  const [subscriptions, setSubscriptions] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const token = localStorage.getItem("token");

  const cargarDatos = useCallback(async () => {
    if (!token) return;
    setIsLoading(true);
    setError("");
    try {
      const datos = await listarSuscripciones(token);
      const suscripcionesAdaptadas = await Promise.all(
        datos.map(async (suscripcion) => {
          const adaptada = adaptarSuscripcion(suscripcion);
          const conversion = await convertirAMoneda(
            adaptada.amount,
            adaptada.currency,
          );
          return { ...adaptada, amountClp: conversion.monto_convertido };
        }),
      );
      setSubscriptions(suscripcionesAdaptadas);
    } catch (requestError) {
      setError(requestError.message || "No se pudieron cargar las suscripciones.");
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  useEffect(() => {
    queueMicrotask(cargarDatos);
  }, [cargarDatos]);

  const activeSubscriptions = subscriptions.filter(
    (subscription) => subscription.isActive
  );

  const getNextBillingDate = (billingDay, today) => {
    const nextDate = new Date(today.getFullYear(), today.getMonth(), billingDay);
    if (nextDate < today) {
      return new Date(today.getFullYear(), today.getMonth() + 1, billingDay);
    }
    return nextDate;
  };

  const upcomingCharges = useMemo(() => {
    const today = new Date();

    return activeSubscriptions
      .map((subscription) => {
        const date = subscription.nextBillingDate || getNextBillingDate(subscription.billingDay, today);
        const diffDays = Math.ceil((date - today) / (1000 * 60 * 60 * 24));
        return { ...subscription, nextDate: date, diffDays };
      })
      .filter((item) => item.diffDays >= 0 && item.diffDays <= 5)
      .sort((a, b) => a.diffDays - b.diffDays);
  }, [activeSubscriptions]);

  const monthlyPayments = useMemo(() => {
    const today = new Date();

    return activeSubscriptions.filter((subscription) => {
      if (subscription.frequency === "Mensual") return true;
      return subscription.nextBillingDate?.getMonth() === today.getMonth();
    });
  }, [activeSubscriptions]);

  const totalMonthlySpend = Math.round(
    monthlyPayments.reduce((total, subscription) => {
      const billingDay = subscription.billingDay;
      return billingDay <= new Date().getDate()
        ? total + Number(subscription.amountClp || 0)
        : total;
    }, 0),
  );

  const projectedSpend = Math.round(
    monthlyPayments.reduce((total, subscription) => {
      return total + Number(subscription.amountClp || 0);
    }, 0),
  ) - totalMonthlySpend;

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;
    setForm((current) => ({
      ...current,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!token || form.id) return;

    try {
      await crearSuscripcion(token, {
        nombre_servicio: form.name.trim(),
        monto_original: Number(form.amount),
        moneda_original: form.currency,
        fecha_proximo_cobro: proximaFecha(Number(form.billingDay)),
        periodicidad: form.frequency === "Anual" ? "anual" : "mensual",
      });
      setForm(initialForm);
      await cargarDatos();
    } catch (requestError) {
      setError(requestError.message || "No se pudo crear la suscripción.");
    }
  };

  const resetForm = () => setForm(initialForm);

  const handleEdit = (item) => {
    setForm({
      id: item.id,
      name: item.name,
      amount: String(item.amount),
      currency: item.currency,
      frequency: item.frequency,
      billingDay: String(item.billingDay),
      isActive: item.isActive,
    });
  };

  const toggleSubscription = async (id) => {
    try {
      await desactivarSuscripcion(token, id);
      await cargarDatos();
    } catch (requestError) {
      setError(requestError.message || "No se pudo desactivar la suscripción.");
    }
  };

  return {
    subscriptions,
    activeSubscriptions,
    form,
    totalMonthlySpend,
    upcomingCharges,
    handleChange,
    handleSubmit,
    resetForm,
    handleEdit,
    toggleSubscription,
    projectedSpend,
    isLoading,
    error,
  };
}

function adaptarSuscripcion(subscription) {
  const date = new Date(`${subscription.fecha_proximo_cobro}T00:00:00`);
  return {
    id: subscription.id,
    name: subscription.nombre_servicio,
    amount: subscription.monto_original,
    currency: subscription.moneda_original,
    frequency: subscription.periodicidad === "anual" ? "Anual" : "Mensual",
    billingDay: date.getDate(),
    nextBillingDate: date,
    isActive: subscription.activa,
  };
}

function proximaFecha(dia) {
  const hoy = new Date();
  const fecha = new Date(hoy.getFullYear(), hoy.getMonth(), dia);
  if (fecha < hoy) fecha.setMonth(fecha.getMonth() + 1);
  return fecha.toISOString().slice(0, 10);
}
